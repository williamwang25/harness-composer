from __future__ import annotations

from importlib import resources

import yaml

from minisweagent.harness_composer.library.schemas.policy_schema import HarnessPolicy

_LIBRARY_PACKAGE = "minisweagent.harness_composer.library"
_POLICY_DIR = "policies"
_PROMPT_DIR = "prompt_fragments"


def _resource_text(dirname: str, filename: str) -> str:
    path = resources.files(_LIBRARY_PACKAGE).joinpath(dirname, filename)
    if not path.is_file():
        raise FileNotFoundError(f"Missing harness library resource: {dirname}/{filename}")
    return path.read_text(encoding="utf-8")


def list_policy_names() -> list[str]:
    policy_dir = resources.files(_LIBRARY_PACKAGE).joinpath(_POLICY_DIR)
    return sorted(path.name.removesuffix(".yaml") for path in policy_dir.iterdir() if path.name.endswith(".yaml"))


def load_policy(policy_name: str) -> HarnessPolicy:
    text = _resource_text(_POLICY_DIR, f"{policy_name}.yaml")
    data = yaml.safe_load(text) or {}
    return HarnessPolicy.model_validate(data)


def get_prompt_fragment(fragment_name: str) -> str:
    filename = fragment_name if fragment_name.endswith(".md") else f"{fragment_name}.md"
    return _resource_text(_PROMPT_DIR, filename).strip()
