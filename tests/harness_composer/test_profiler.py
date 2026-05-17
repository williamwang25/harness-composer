from minisweagent.harness_composer.profiler.repo_task_profiler import RepoTaskProfiler


def test_profiles_python_pytest_repo(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "demo.py").write_text("def add(a, b):\n    return a + b\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_demo.py").write_text("def test_add():\n    assert True\n")

    profile = RepoTaskProfiler().profile(tmp_path, "Fix the failing pytest regression")

    assert profile.language == "python"
    assert profile.build_system == "pyproject"
    assert profile.test_framework == "pytest"
    assert profile.task_type == "test_update"
    assert profile.verification_type == "unit_test"
    assert profile.likely_test_command == "pytest -q"


def test_profiles_node_repo(tmp_path):
    (tmp_path / "package.json").write_text('{"scripts": {"test": "jest"}}')
    (tmp_path / "index.ts").write_text("export const value = 1;\n")

    profile = RepoTaskProfiler().profile(tmp_path, "Implement support for a new option")

    assert profile.language == "typescript"
    assert profile.build_system == "package.json"
    assert profile.test_framework == "npm"
    assert profile.likely_test_command == "npm test"
