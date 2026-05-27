# Harness Composer Results

This document organizes the figures and aggregate result tables extracted from the EMNLP paper draft.
It is intended as the project-facing companion to the README: the README shows the headline story,
while this file keeps the table-level evidence easy to inspect on GitHub.

## Figure Inventory

| Figure | PNG preview | PDF source | Supports |
| --- | --- | --- | --- |
| Architecture overview | [overview.png](assets/figures/overview.png) | [overview.pdf](assets/figures/overview.pdf) | Profiler, router, module library, composer, runtime loop, and decision manifest. |
| Terminal-Bench 2 main results | [terminal-bench-results.png](assets/figures/terminal-bench-results.png) | [terminal-bench-results.pdf](assets/figures/terminal-bench-results.pdf) | Top-line Terminal-Bench 2 comparison and Mini-SWE-Agent baseline comparison. |
| Ablation and efficiency | [ablation-efficiency.png](assets/figures/ablation-efficiency.png) | [ablation-efficiency.pdf](assets/figures/ablation-efficiency.pdf) | Accuracy, cost, cache, and compression trade-offs on Terminal-Bench 2 and SWE-bench Verified-100. |

## Main Terminal-Bench 2 Results

Full 89-task Terminal-Bench 2 evaluation with 5 trials per task.

| Agent | Model | Accuracy (%) |
| --- | --- | ---: |
| Harness Composer | Claude Opus 4.6 | 65.2 +/- 2.6 |
| Terminus 2 | Claude Opus 4.6 | 62.9 +/- 2.7 |
| Claude Code | Claude Opus 4.6 | 58.0 +/- 2.9 |
| Mini-SWE-Agent | Claude Opus 4.6 | 57.3 +/- 2.8 |
| Mini-SWE-Agent | Claude Sonnet 4.5 | 42.5 +/- 2.8 |
| Mini-SWE-Agent | GPT-5-Codex | 41.3 +/- 2.8 |
| Claude Code | Claude Sonnet 4.5 | 40.1 +/- 2.9 |
| Terminus 2 | Claude Opus 4.1 | 38.0 +/- 2.6 |
| OpenHands | Claude Opus 4.1 | 36.9 +/- 2.7 |
| Mini-SWE-Agent | Claude Opus 4.1 | 35.1 +/- 2.5 |
| Mini-SWE-Agent | GPT-5 | 33.9 +/- 2.9 |

## Controlled Terminal-Bench 2 Comparison

All variants use the same Mini-SWE-Agent runtime and Claude Opus 4.6.

| Variant | Accuracy (%) | Cost (USD/task) | Input tokens (M) | Cache hit (%) |
| --- | ---: | ---: | ---: | ---: |
| Base | 57.3 | 0.382 | 10.2 | 54.1 |
| Fixed Lean | 59.6 | 0.351 | 9.1 | 62.8 |
| All-Tools | 60.7 | 0.372 | 9.8 | 57.6 |
| Harness Composer | 65.2 | 0.317 | 8.5 | 75.7 |

## SWE-bench Verified-100

Claude Opus 4.6 on a 100-task descriptor subset.

| Variant | Pass@1 (%) | Cost (USD/task) | Input tokens (M) | Compression |
| --- | ---: | ---: | ---: | ---: |
| Base | 78.0 | 0.750 | 2.15 | - |
| Fixed Lean | 78.0 | 0.706 | 1.98 | 1.7x |
| All-Tools | 74.0 | 0.813 | 2.34 | 1.3x |
| Harness Composer | 80.0 | 0.694 | 1.82 | 2.4x |

## Cross-Model Generalization

Terminal-Bench 2 comparison between vanilla Mini-SWE-Agent and Harness Composer.

| Model | Base (%) | Harness Composer (%) | Delta |
| --- | ---: | ---: | ---: |
| Claude Opus 4.6 | 57.3 | 65.2 | +7.9 |
| Claude Sonnet 4.5 | 42.5 | 50.6 | +8.1 |
| Claude Opus 4.1 | 35.1 | 43.8 | +8.7 |
| GPT-5 | 33.9 | 42.7 | +8.8 |
| GPT-5-Mini | 22.2 | 29.2 | +7.0 |

## Ablation Study

Terminal-Bench 2 with Claude Opus 4.6. Each row removes one component from the full system.

| Variant | Accuracy (%) | Delta | Cost (USD/task) |
| --- | ---: | ---: | ---: |
| Full Harness Composer | 65.2 | - | 0.317 |
| - Profiler | 57.3 | -7.9 | 0.369 |
| - Router | 59.6 | -5.6 | 0.352 |
| - Compression | 60.7 | -4.5 | 0.381 |
| - Context Policy | 62.9 | -2.3 | 0.341 |
| - Control Policy | 64.0 | -1.2 | 0.331 |
| - Memory/State | 64.6 | -0.6 | 0.321 |

## Composition Strategy

All variants use the same module library.

| Strategy | Accuracy (%) | Cost (USD/task) | Tokens (K/task) |
| --- | ---: | ---: | ---: |
| All-Tools | 60.7 | 0.372 | 124.3 |
| Random Policy | 57.3 | 0.369 | 113.7 |
| Harness Composer | 65.2 | 0.317 | 101.5 |

## Cost-Performance

Terminal-Bench 2 with Claude Opus 4.6.

| Variant | Accuracy (%) | Cost (USD/task) | Cost per success (USD) | Tokens per success (K) |
| --- | ---: | ---: | ---: | ---: |
| Base | 57.3 | 0.382 | 0.667 | 248.3 |
| Fixed Lean | 59.6 | 0.351 | 0.589 | 215.1 |
| All-Tools | 60.7 | 0.372 | 0.613 | 227.8 |
| Harness Composer | 65.2 | 0.317 | 0.486 | 155.4 |

## Terminal-Bench 2 Policy Routing

| Policy | Tasks | Resolved | Accuracy (%) |
| --- | ---: | ---: | ---: |
| `terminal_task` | 77 | 53 | 68.8 |
| `small_repo_direct` | 8 | 4 | 50.0 |
| `fallback` | 4 | 1 | 25.0 |
| Total | 89 | 58 | 65.2 |

## SWE-bench Verified-100 Policy Routing

| Policy | Tasks | Resolved | Accuracy (%) |
| --- | ---: | ---: | ---: |
| `python_large_repo` | 44 | 36 | 81.8 |
| `python_pytest` | 36 | 28 | 77.8 |
| `small_repo_direct` | 14 | 12 | 85.7 |
| `fallback` | 6 | 4 | 66.7 |
| Total | 100 | 80 | 80.0 |

## Observation Compression

| Benchmark | Original chars | Compressed chars | Ratio |
| --- | ---: | ---: | ---: |
| Terminal-Bench 2 | 14,238 | 5,085 | 2.8x |
| SWE-bench Verified-100 | 11,462 | 4,408 | 2.6x |

## SWE-bench Verified-100 Repository Distribution

| Repository | Tasks |
| --- | ---: |
| django/django | 42 |
| sympy/sympy | 14 |
| sphinx-doc/sphinx | 9 |
| matplotlib/matplotlib | 7 |
| scikit-learn/scikit-learn | 7 |
| astropy/astropy | 5 |
| pydata/xarray | 5 |
| pytest-dev/pytest | 4 |
| pylint-dev/pylint | 3 |
| psf/requests | 2 |
| mwaskom/seaborn | 1 |
| pallets/flask | 1 |
| Total | 100 |
