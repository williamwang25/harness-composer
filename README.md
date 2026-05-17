# Harness Composer

Harness Composer is a lightweight research prototype for composing software-engineering agent harnesses around mini-SWE-agent.

The central idea is simple: do not use one fixed harness for every repository. Instead, profile the repository and task first, route that profile to a modular policy, and compose only the prompt fragments, context rules, test guidance, compression behavior, and runtime metadata needed for that instance.

```text
repo/task -> profile -> route policy -> compose config -> run mini-SWE-agent -> save manifest
```

## Status

This repository currently implements the Phase 0/1 prototype:

- deterministic repo/task profiler;
- rule-based policy router;
- small YAML policy library;
- prompt fragment composer;
- generated mini-SWE-agent config;
- decision manifest for auditability;
- optional runtime adapter for long-output compression and repeated-command tracking;
- tests for profiler, router, policy loading, composer, and compression.

It intentionally does not implement full self-evolution, arbitrary harness-code search, or large-scale learned routing.

## Why

Many coding-agent improvements come from the harness around the model: what context is shown, which tools are encouraged, how tests are run, how long outputs are compressed, and what state is preserved.

Harness Composer tests this research hypothesis:

> A small, typed library of harness modules can be adaptively composed according to repo/task profiles, yielding better cost-performance trade-offs than a fixed mini-SWE-agent harness or an all-tools/all-context harness.

## Quick Start

Use the conda environment prepared for this workspace:

```powershell
conda activate sweworld
```

Generate a composed config and decision manifest:

```powershell
python -m minisweagent.harness_composer.cli compose `
  ..\SWE-bench Verified-50\repos\psf__requests `
  -t "Fix a failing pytest issue" `
  --task-id psf_requests_smoke `
  -o .\harness.generated.yaml `
  -m .\decision_manifest.json `
  --print-manifest
```

Then pass the generated config to mini-SWE-agent:

```powershell
mini -c .\harness.generated.yaml -y
```

The package also exposes a CLI alias when installed:

```powershell
harness-compose compose <repo> -t "<task>" -o harness.generated.yaml -m decision_manifest.json
```

## Built-in Policies

The initial policy library includes:

- `fallback`
- `small_repo_direct`
- `python_pytest`
- `python_large_repo`
- `js_node`
- `go_static`
- `terminal_task`
- `all_tools`

The key ablation is `all_tools` vs routed Harness Composer. The goal is to test whether the right modular composition beats simply exposing every module.

## Project Layout

```text
src/minisweagent/harness_composer/
  profiler/          repo/task profiling
  router/            rule-based policy routing
  library/           YAML policies and prompt fragments
  composer/          config and manifest composition
  adapters/          mini-SWE-agent runtime adapter
  runtime/           observation compression helpers
  cli.py             compose/profile commands
tests/harness_composer/
```

## Verification

Targeted tests used during the initial implementation:

```powershell
conda run -n sweworld python -m pytest tests\harness_composer tests\agents\test_init.py -q
```

Expected current result:

```text
19 passed
```

## Attribution

Harness Composer is built on top of mini-SWE-agent and keeps the underlying `minisweagent` runtime package for compatibility. The research layer added here focuses on modular harness composition, routing, manifests, and cost-aware observation handling.
