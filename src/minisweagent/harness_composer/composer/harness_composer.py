from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from minisweagent.config import get_config_from_spec
from minisweagent.harness_composer.composer.manifest import build_manifest, save_manifest
from minisweagent.harness_composer.composer.prompt_builder import PromptBuilder
from minisweagent.harness_composer.library.policy_loader import load_policy
from minisweagent.harness_composer.library.schemas.policy_schema import HarnessPolicy
from minisweagent.harness_composer.profiler.repo_task_profiler import RepoTaskProfiler
from minisweagent.harness_composer.profiler.schema import RepoTaskProfile
from minisweagent.harness_composer.router.policy_router import PolicyRouter, RoutingDecision
from minisweagent.utils.serialize import recursive_merge


class HarnessComposerConfig(BaseModel):
    base_config_specs: list[str] = ["mini"]
    use_harness_agent: bool = True
    force_policy: str | None = None
    task_id: str = "adhoc_task"


class ComposedHarness(BaseModel):
    profile: RepoTaskProfile
    routing: RoutingDecision
    policy: HarnessPolicy
    config: dict[str, Any]
    manifest: dict[str, Any]


class HarnessComposer:
    """Compose a runnable mini-SWE-agent config from a repo/task profile."""

    def __init__(
        self,
        *,
        profiler: RepoTaskProfiler | None = None,
        router: PolicyRouter | None = None,
        prompt_builder: PromptBuilder | None = None,
    ):
        self.profiler = profiler or RepoTaskProfiler()
        self.router = router or PolicyRouter()
        self.prompt_builder = prompt_builder or PromptBuilder()

    def compose(
        self,
        *,
        repo_path: str | Path,
        task: str = "",
        config: HarnessComposerConfig | None = None,
        base_config: dict[str, Any] | None = None,
        output_config_path: Path | None = None,
        manifest_path: Path | None = None,
    ) -> ComposedHarness:
        composer_config = config or HarnessComposerConfig()
        profile = self.profiler.profile(repo_path, task)
        routing = self.router.route(profile)
        if composer_config.force_policy:
            routing = RoutingDecision(
                selected_policy=composer_config.force_policy,
                reason=f"Policy forced by caller: {composer_config.force_policy}.",
                considered_rules=routing.considered_rules,
            )
        policy = load_policy(routing.selected_policy)
        mini_config = self._load_base_config(composer_config, base_config)
        composed_config = self._compose_config(
            mini_config=mini_config,
            repo_path=Path(repo_path).resolve(),
            task=task,
            profile=profile,
            routing=routing,
            policy=policy,
            composer_config=composer_config,
            manifest_path=manifest_path,
        )
        manifest = build_manifest(
            task_id=composer_config.task_id,
            profile=profile,
            policy=policy,
            routing=routing,
            config_path=str(output_config_path) if output_config_path else None,
        )
        if output_config_path:
            self.save_config(composed_config, output_config_path)
        if manifest_path:
            save_manifest(manifest, manifest_path)
        return ComposedHarness(
            profile=profile,
            routing=routing,
            policy=policy,
            config=composed_config,
            manifest=manifest,
        )

    @staticmethod
    def save_config(config: dict[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=False), encoding="utf-8")

    @staticmethod
    def _load_base_config(composer_config: HarnessComposerConfig, base_config: dict[str, Any] | None) -> dict[str, Any]:
        if base_config is not None:
            return copy.deepcopy(base_config)
        configs = [get_config_from_spec(spec) for spec in composer_config.base_config_specs]
        return recursive_merge(*configs)

    def _compose_config(
        self,
        *,
        mini_config: dict[str, Any],
        repo_path: Path,
        task: str,
        profile: RepoTaskProfile,
        routing: RoutingDecision,
        policy: HarnessPolicy,
        composer_config: HarnessComposerConfig,
        manifest_path: Path | None,
    ) -> dict[str, Any]:
        prompt_addendum = self.prompt_builder.build(profile=profile, policy=policy, routing=routing)
        current_instance_template = mini_config.get("agent", {}).get("instance_template", "")
        agent_config: dict[str, Any] = {
            "instance_template": f"{current_instance_template.rstrip()}\n\n{prompt_addendum}\n",
            "harness_composer": {
                "enabled": True,
                "policy_name": policy.policy_name,
                "policy": policy.model_dump(mode="json"),
                "profile": profile.model_dump(mode="json"),
                "routing": routing.model_dump(mode="json"),
                "manifest_path": str(manifest_path) if manifest_path else "",
            },
        }
        if composer_config.use_harness_agent:
            agent_config["agent_class"] = "harness_composer"
        max_turns = policy.control_policy.get("max_turns")
        if max_turns and not mini_config.get("agent", {}).get("step_limit"):
            agent_config["step_limit"] = max_turns

        env_config = {"cwd": str(repo_path)}
        run_config = {"task": task}
        metadata_config = {
            "harness_composer": {
                "task_id": composer_config.task_id,
                "selected_policy": policy.policy_name,
                "router_reason": routing.reason,
                "profile": profile.compact_dict(),
            }
        }
        return recursive_merge(
            mini_config,
            {"agent": agent_config, "environment": env_config, "run": run_config},
            metadata_config,
        )

    @staticmethod
    def to_json(composed: ComposedHarness) -> str:
        return json.dumps(composed.model_dump(mode="json"), indent=2, sort_keys=True)
