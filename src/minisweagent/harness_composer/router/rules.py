from __future__ import annotations

from collections.abc import Callable

from minisweagent.harness_composer.profiler.schema import RepoTaskProfile

PolicyRule = Callable[[RepoTaskProfile], tuple[str, str] | None]


def terminal_task_rule(profile: RepoTaskProfile) -> tuple[str, str] | None:
    if profile.task_type == "terminal_task":
        return "terminal_task", "Task language indicates a terminal or shell workflow."
    return None


def python_large_repo_rule(profile: RepoTaskProfile) -> tuple[str, str] | None:
    if profile.language == "python" and profile.repo_scale == "large":
        return "python_large_repo", "Large Python repository; route to search-first and compressed-output policy."
    return None


def python_pytest_rule(profile: RepoTaskProfile) -> tuple[str, str] | None:
    if profile.language == "python" and profile.test_framework == "pytest":
        return "python_pytest", "Python repository with pytest signals."
    return None


def javascript_rule(profile: RepoTaskProfile) -> tuple[str, str] | None:
    if profile.language in {"javascript", "typescript"}:
        return "js_node", "JavaScript or TypeScript project with Node-style verification."
    return None


def go_rule(profile: RepoTaskProfile) -> tuple[str, str] | None:
    if profile.language == "go":
        return "go_static", "Go repository; prefer go test and static package navigation."
    return None


def small_repo_rule(profile: RepoTaskProfile) -> tuple[str, str] | None:
    if profile.repo_scale in {"tiny", "small"}:
        return "small_repo_direct", "Small repository; direct file inspection should stay within context budget."
    return None


DEFAULT_RULES: list[PolicyRule] = [
    terminal_task_rule,
    python_large_repo_rule,
    python_pytest_rule,
    javascript_rule,
    go_rule,
    small_repo_rule,
]
