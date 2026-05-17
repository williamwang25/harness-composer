from __future__ import annotations

from pydantic import BaseModel, Field

from minisweagent.harness_composer.profiler.schema import RepoTaskProfile
from minisweagent.harness_composer.router.rules import DEFAULT_RULES, PolicyRule


class RoutingDecision(BaseModel):
    selected_policy: str
    reason: str
    considered_rules: list[str] = Field(default_factory=list)


class PolicyRouter:
    """Rule-based router from repo/task profile to a modular harness policy."""

    def __init__(self, rules: list[PolicyRule] | None = None, *, fallback_policy: str = "fallback"):
        self.rules = rules or DEFAULT_RULES
        self.fallback_policy = fallback_policy

    def route(self, profile: RepoTaskProfile) -> RoutingDecision:
        considered_rules: list[str] = []
        for rule in self.rules:
            considered_rules.append(rule.__name__)
            result = rule(profile)
            if result is not None:
                policy, reason = result
                return RoutingDecision(
                    selected_policy=policy,
                    reason=reason,
                    considered_rules=considered_rules,
                )
        return RoutingDecision(
            selected_policy=self.fallback_policy,
            reason="No specialized routing rule matched; using fallback policy.",
            considered_rules=considered_rules,
        )
