from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HarnessPolicy(BaseModel):
    """A modular recipe for composing a mini-SWE-agent harness."""

    policy_name: str
    description: str = ""
    prompt_fragments: list[str] = Field(default_factory=list)
    tool_kernel: list[str] = Field(default_factory=list)
    context_policy: dict[str, Any] = Field(default_factory=dict)
    test_policy: dict[str, Any] = Field(default_factory=dict)
    compression_policy: dict[str, Any] = Field(default_factory=dict)
    control_policy: dict[str, Any] = Field(default_factory=dict)
    memory_policy: dict[str, Any] = Field(default_factory=dict)
    expected_benefit: str = ""
    risk: str = ""

    @property
    def enabled_modules(self) -> list[str]:
        modules = list(self.tool_kernel)
        for name, value in {
            "context_policy": self.context_policy,
            "test_policy": self.test_policy,
            "compression_policy": self.compression_policy,
            "control_policy": self.control_policy,
            "memory_policy": self.memory_policy,
        }.items():
            if value:
                modules.append(name)
        return modules
