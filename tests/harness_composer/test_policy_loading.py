from minisweagent.harness_composer.library.policy_loader import get_prompt_fragment, list_policy_names, load_policy


def test_loads_builtin_policy():
    policy = load_policy("python_pytest")

    assert policy.policy_name == "python_pytest"
    assert "run_test" in policy.tool_kernel
    assert "compression_policy" in policy.enabled_modules


def test_lists_builtin_policies_and_fragments():
    policy_names = list_policy_names()
    fragment = get_prompt_fragment("base")

    assert "fallback" in policy_names
    assert "python_large_repo" in policy_names
    assert "Harness Composer Policy" in fragment
