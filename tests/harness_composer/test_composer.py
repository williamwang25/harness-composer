import json

import yaml

from minisweagent.harness_composer.composer.harness_composer import HarnessComposer, HarnessComposerConfig


def test_composer_writes_config_and_manifest(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
    (repo / "demo.py").write_text("def f():\n    return 1\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_demo.py").write_text("def test_f():\n    assert True\n")
    output_config = tmp_path / "generated.yaml"
    manifest_path = tmp_path / "manifest.json"
    base_config = {
        "agent": {
            "system_template": "system",
            "instance_template": "Task: {{task}}",
            "step_limit": 0,
            "cost_limit": 1.0,
            "mode": "yolo",
        },
        "model": {"observation_template": "{{ output.output }}"},
        "environment": {},
    }

    composed = HarnessComposer().compose(
        repo_path=repo,
        task="Fix a failing pytest issue",
        config=HarnessComposerConfig(task_id="demo_task"),
        base_config=base_config,
        output_config_path=output_config,
        manifest_path=manifest_path,
    )

    assert composed.policy.policy_name == "python_pytest"
    assert composed.config["agent"]["agent_class"] == "harness_composer"
    assert composed.config["agent"]["step_limit"] == 40
    assert "Selected Harness Recipe" in composed.config["agent"]["instance_template"]
    assert composed.config["environment"]["cwd"] == str(repo.resolve())
    assert output_config.exists()
    assert manifest_path.exists()
    assert yaml.safe_load(output_config.read_text())["agent"]["harness_composer"]["policy_name"] == "python_pytest"
    manifest = json.loads(manifest_path.read_text())
    assert manifest["task_id"] == "demo_task"
    assert manifest["selected_policy"] == "python_pytest"
