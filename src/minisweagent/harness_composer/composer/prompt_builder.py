from __future__ import annotations

import json

from minisweagent.harness_composer.library.policy_loader import get_prompt_fragment
from minisweagent.harness_composer.library.schemas.policy_schema import HarnessPolicy
from minisweagent.harness_composer.profiler.schema import RepoTaskProfile
from minisweagent.harness_composer.router.policy_router import RoutingDecision


class PromptBuilder:
    """Build prompt addenda from policy fragments and routing metadata."""

    def build(self, *, profile: RepoTaskProfile, policy: HarnessPolicy, routing: RoutingDecision) -> str:
        fragments = [get_prompt_fragment(fragment) for fragment in policy.prompt_fragments]
        policy_block = self._policy_block(profile=profile, policy=policy, routing=routing)
        return "\n\n".join([*fragments, policy_block]).strip()

    @staticmethod
    def _policy_block(*, profile: RepoTaskProfile, policy: HarnessPolicy, routing: RoutingDecision) -> str:
        profile_json = json.dumps(profile.compact_dict(), indent=2, sort_keys=True)
        policy_json = json.dumps(
            {
                "policy_name": policy.policy_name,
                "tool_kernel": policy.tool_kernel,
                "context_policy": policy.context_policy,
                "test_policy": policy.test_policy,
                "compression_policy": policy.compression_policy,
                "control_policy": policy.control_policy,
                "memory_policy": policy.memory_policy,
            },
            indent=2,
            sort_keys=True,
        )
        return f"""## Selected Harness Recipe

Router reason: {routing.reason}

Repository/task profile:

```json
{profile_json}
```

Policy recipe:

```json
{policy_json}
```

Expected benefit: {policy.expected_benefit}
Known risk: {policy.risk}
"""
