from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from minisweagent.agents.interactive import InteractiveAgent, InteractiveAgentConfig
from minisweagent.exceptions import Submitted
from minisweagent.harness_composer.runtime.observation_compressor import compress_output
from minisweagent.utils.serialize import recursive_merge


class HarnessRuntimeConfig(BaseModel):
    enabled: bool = True
    policy_name: str = ""
    policy: dict[str, Any] = Field(default_factory=dict)
    profile: dict[str, Any] = Field(default_factory=dict)
    routing: dict[str, Any] = Field(default_factory=dict)
    manifest_path: str = ""
    compression_max_chars: int = 6000


class HarnessComposerAgentConfig(InteractiveAgentConfig):
    harness_composer: HarnessRuntimeConfig = Field(default_factory=HarnessRuntimeConfig)


class HarnessComposerAgent(InteractiveAgent):
    """InteractiveAgent with lightweight harness-runtime behaviors."""

    def __init__(self, *args, config_class=HarnessComposerAgentConfig, **kwargs):
        super().__init__(*args, config_class=config_class, **kwargs)
        self.command_counts: dict[str, int] = {}
        self.compression_stats: list[dict[str, Any]] = []

    def execute_actions(self, message: dict) -> list[dict]:
        actions = message.get("extra", {}).get("actions", [])
        commands = [action["command"] for action in actions]
        outputs = []
        try:
            self._ask_confirmation_or_interrupt(commands)
            for action in actions:
                command = action.get("command", "")
                output = self.env.execute(action)
                outputs.append(self._process_output(command, output))
        except Submitted as e:
            self._check_for_new_task_or_submit(e)
        finally:
            result = self.add_messages(
                *self.model.format_observation_messages(message, outputs, self.get_template_vars())
            )
        return result

    def _process_output(self, command: str, output: dict) -> dict:
        runtime_config = self.config.harness_composer
        self.command_counts[command] = self.command_counts.get(command, 0) + 1
        output = dict(output)
        if not runtime_config.enabled:
            return output

        strategy = self._compression_strategy(command, output)
        text = output.get("output", "")
        if strategy:
            compressed, stats = compress_output(
                text,
                strategy=strategy,
                max_chars=runtime_config.compression_max_chars,
            )
            output["output"] = compressed
            output.setdefault("extra", {})
            output["extra"] |= {
                "harness_output_compressed": stats.compressed,
                "harness_original_output_chars": stats.original_chars,
                "harness_compressed_output_chars": stats.compressed_chars,
                "harness_compression_strategy": stats.strategy,
            }
            if stats.compressed:
                self.compression_stats.append(output["extra"].copy())

        if self._should_warn_repeated(command):
            output["output"] = (
                f"[Harness Composer warning: repeated command run #{self.command_counts[command]}]\n"
                f"{output.get('output', '')}"
            )
        return output

    def _compression_strategy(self, command: str, output: dict) -> str:
        policy = self.config.harness_composer.policy
        compression_policy = policy.get("compression_policy", {})
        if not compression_policy:
            return ""
        text = output.get("output", "")
        command_lower = command.lower()
        if compression_policy.get("pytest") and ("pytest" in command_lower or "short test summary info" in text):
            return "traceback_assertion_only"
        if compression_policy.get("generic"):
            return "tail_and_error_blocks"
        return ""

    def _should_warn_repeated(self, command: str) -> bool:
        policy = self.config.harness_composer.policy
        control_policy = policy.get("control_policy", {})
        return bool(control_policy.get("repeated_command_warning") and self.command_counts.get(command, 0) > 1)

    def serialize(self, *extra_dicts) -> dict:
        harness_data = {
            "info": {
                "harness_composer": {
                    "policy_name": self.config.harness_composer.policy_name,
                    "manifest_path": self.config.harness_composer.manifest_path,
                    "compression_events": len(self.compression_stats),
                    "repeated_commands": {
                        command: count for command, count in self.command_counts.items() if count > 1
                    },
                }
            }
        }
        return recursive_merge(super().serialize(*extra_dicts), harness_data)
