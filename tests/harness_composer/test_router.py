from minisweagent.harness_composer.profiler.schema import RepoTaskProfile
from minisweagent.harness_composer.router.policy_router import PolicyRouter


def test_routes_large_python_first():
    profile = RepoTaskProfile(
        repo_path="/repo",
        language="python",
        test_framework="pytest",
        repo_scale="large",
        task_type="bug_fix",
    )

    decision = PolicyRouter().route(profile)

    assert decision.selected_policy == "python_large_repo"
    assert "Large Python" in decision.reason


def test_routes_python_pytest():
    profile = RepoTaskProfile(
        repo_path="/repo",
        language="python",
        test_framework="pytest",
        repo_scale="small",
        task_type="bug_fix",
    )

    decision = PolicyRouter().route(profile)

    assert decision.selected_policy == "python_pytest"


def test_routes_terminal_task_before_language_rules():
    profile = RepoTaskProfile(
        repo_path="/repo",
        language="python",
        test_framework="pytest",
        repo_scale="large",
        task_type="terminal_task",
    )

    decision = PolicyRouter().route(profile)

    assert decision.selected_policy == "terminal_task"
