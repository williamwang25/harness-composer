from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

RepoScale = Literal["tiny", "small", "medium", "large"]
TaskType = Literal["bug_fix", "feature", "test_update", "docs", "terminal_task", "unknown"]
VerificationType = Literal["unit_test", "integration_test", "lint", "manual", "unknown"]


class RepoTaskProfile(BaseModel):
    """A compact, deterministic summary used for policy routing."""

    repo_path: str
    task_preview: str = ""
    language: str = "unknown"
    languages: list[str] = Field(default_factory=list)
    build_system: str = "unknown"
    test_framework: str = "unknown"
    repo_scale: RepoScale = "small"
    task_type: TaskType = "unknown"
    verification_type: VerificationType = "unknown"
    likely_test_command: str = ""
    context_risk: list[str] = Field(default_factory=list)
    evidence: dict[str, object] = Field(default_factory=dict)

    def compact_dict(self) -> dict:
        """Return the fields that should appear in prompts and manifests."""
        return self.model_dump(exclude={"evidence"})
