from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from minisweagent.harness_composer.composer.harness_composer import HarnessComposer, HarnessComposerConfig
from minisweagent.harness_composer.profiler.repo_task_profiler import RepoTaskProfiler

console = Console(highlight=False)
app = typer.Typer(help="Compose modular mini-SWE-agent harness configs.")


@app.command()
def profile(
    repo: Annotated[Path, typer.Argument(help="Repository path to inspect.")],
    task: Annotated[str, typer.Option("-t", "--task", help="Task/problem statement.")] = "",
) -> None:
    """Print the deterministic repo/task profile."""
    repo_profile = RepoTaskProfiler().profile(repo, task)
    console.print_json(json.dumps(repo_profile.model_dump(mode="json"), indent=2))


@app.command()
def compose(
    repo: Annotated[Path, typer.Argument(help="Repository path the agent will work in.")],
    task: Annotated[str, typer.Option("-t", "--task", help="Task/problem statement.")] = "",
    task_id: Annotated[str, typer.Option("--task-id", help="Identifier written to the decision manifest.")] = "adhoc_task",
    output_config: Annotated[
        Path,
        typer.Option("-o", "--output-config", help="Path for the generated mini-SWE-agent YAML config."),
    ] = Path("harness_composer.generated.yaml"),
    manifest: Annotated[
        Path,
        typer.Option("-m", "--manifest", help="Path for the decision manifest JSON."),
    ] = Path("decision_manifest.json"),
    base_config: Annotated[
        list[str],
        typer.Option("-c", "--config", help="Base mini-SWE-agent config spec(s) to merge before composing."),
    ] = ["mini"],
    force_policy: Annotated[str | None, typer.Option("--policy", help="Force a policy instead of routing.")] = None,
    no_harness_agent: Annotated[
        bool,
        typer.Option("--no-harness-agent", help="Only compose prompts/config; do not enable runtime adapter."),
    ] = False,
    print_manifest: Annotated[
        bool,
        typer.Option("--print-manifest", help="Print the generated manifest after writing files."),
    ] = False,
) -> None:
    """Write a composed config and manifest that can be passed to `mini -c`."""
    composer = HarnessComposer()
    composed = composer.compose(
        repo_path=repo,
        task=task,
        config=HarnessComposerConfig(
            base_config_specs=base_config,
            use_harness_agent=not no_harness_agent,
            force_policy=force_policy,
            task_id=task_id,
        ),
        output_config_path=output_config,
        manifest_path=manifest,
    )
    console.print(f"Selected policy: [bold green]{composed.policy.policy_name}[/bold green]")
    console.print(f"Router reason: {composed.routing.reason}")
    console.print(f"Wrote config: [bold green]{output_config}[/bold green]")
    console.print(f"Wrote manifest: [bold green]{manifest}[/bold green]")
    if print_manifest:
        console.print_json(json.dumps(composed.manifest, indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
