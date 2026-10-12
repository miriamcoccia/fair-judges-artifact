"""
cli.py: command-line interface for the MLLM pipeline —
sample / run / analyse.
"""

import typer
import pandas as pd
from pathlib import Path

from data.experiment_sample import build_phase1_sample
from data.scienceqa import ScienceQALoader
from execution.runner import run_pipeline
from execution.cache import Cache
from execution.ledger import Ledger
from execution.planner import plan_work
from evaluation.load import load_results
from evaluation.curves import detection_rate_by_severity
from evaluation.figures import plot_detection_by_severity
from evaluation.tables import detection_rate_table_latex, save_table
from mutations.base import MutationType, Severity
from mutations.fair_representation_pool import build_candidate_pool
from providers.registry import get_provider
from tracking.registry import get_tracker
from config import Secrets, load_pricing, load_all_model_configs

app = typer.Typer()


@app.command()
def sample(
    input_csv: Path = typer.Option(..., help="Path to the full ScienceQA CSV."),
    output_csv: Path = typer.Option(..., help="Where to save the Phase 1 sample."),
    fraction: float = typer.Option(0.1, help="Fraction of the data to sample."),
    stratify_by: str = typer.Option("subject", help="Column to stratify by."),
    seed: int = typer.Option(42, help="Random seed for reproducibility."),
) -> None:
    """Build and save the Phase 1 stratified sample."""
    df = pd.read_csv(input_csv)
    sample_df = build_phase1_sample(df, fraction, stratify_by, seed)
    sample_df.to_csv(output_csv, index=False)
    typer.echo(f"Saved {len(sample_df)} rows to {output_csv}")


@app.command()
def run(
    items_csv: Path = typer.Option(..., help="CSV of items to run the pipeline on."),
    strategies: str = typer.Option("combined", help="Comma-separated: split,combined"),
    models: str = typer.Option(..., help="Comma-separated model names."),
    seed: int = typer.Option(42),
    manifest_path: Path = typer.Option(Path("runs/manifest.json")),
    max_per_batch: int = typer.Option(
        1788, help="Max requests per batch (size-limited by base64 images)."
    ),
    dry_run: bool = typer.Option(
        False, help="Plan the work without submitting anything."
    ),
    cmsc_pool_dir: Path = typer.Option(
        None,
        help=(
            "Root of a local CMSC checkout, used to build the fair_representation "
            "candidate pool. If omitted, fair_representation is left out of the "
            "run entirely, same as before this flag existed."
        ),
    ),
    mutations: str = typer.Option(
        None,
        help=(
            "Comma-separated mutation type values to run, e.g. 'fair_representation' "
            "or 'blur,rotate'. If omitted, falls back to the old default: everything "
            "except fair_representation, unless --cmsc-pool-dir is given."
        ),
    ),
) -> None:
    """Run the pipeline: plan, submit batches, wait, record results."""
    df = pd.read_csv(items_csv)
    loader = ScienceQALoader(df)
    items = loader.load_items()

    strategy_list = strategies.split(",")
    model_list = models.split(",")
    severities = list(Severity)

    fair_representation_candidates: list[str] | None = None
    if cmsc_pool_dir is not None:
        fair_representation_candidates = build_candidate_pool(cmsc_pool_dir)
        if not fair_representation_candidates:
            typer.echo(
                f"Warning: no fair_representation candidates found under {cmsc_pool_dir} "
                "— check the flagged-combinations list matches folders that actually exist. "
                "Continuing without fair_representation."
            )

    if mutations is not None:
        requested_values = mutations.split(",")
        mutation_types = [mt for mt in MutationType if mt.value in requested_values]

        unknown = set(requested_values) - {mt.value for mt in MutationType}
        if unknown:
            typer.echo(f"Unknown mutation type(s): {', '.join(unknown)}")
            raise typer.Exit(code=1)

        if (
            MutationType.FAIR_REPRESENTATION in mutation_types
            and fair_representation_candidates is None
        ):
            typer.echo(
                "fair_representation was requested via --mutations, but "
                "--cmsc-pool-dir was not given. Pass --cmsc-pool-dir to build "
                "the candidate pool."
            )
            raise typer.Exit(code=1)
    elif cmsc_pool_dir is not None:
        mutation_types = list(MutationType)
    else:
        mutation_types = [
            mt for mt in MutationType if mt != MutationType.FAIR_REPRESENTATION
        ]

    if dry_run:
        cache = Cache(Path("runs/cache.txt"))
        planned_units = plan_work(
            items, mutation_types, severities, model_list, strategy_list, cache, seed
        )
        total = (
            len(items)
            * len(mutation_types)
            * len(severities)
            * len(model_list)
            * len(strategy_list)
        )
        typer.echo(
            f"Would run {len(planned_units)} remaining units (out of {total} total; {total - len(planned_units)} already done)."
        )
        return

    secrets = Secrets()
    provider = get_provider("openai", api_key=secrets.openai_api_key)
    pricing = load_pricing(Path("configs/pricing.yaml"))
    cache = Cache(Path("runs/cache.txt"))
    ledger = Ledger(Path("runs/ledger.txt"))
    tracker = get_tracker("mlflow")
    model_configs = load_all_model_configs(Path("configs/models"))

    run_pipeline(
        items=items,
        mutation_types=mutation_types,
        severities=severities,
        models=model_list,
        strategies=strategy_list,
        provider=provider,
        cache=cache,
        ledger=ledger,
        tracker=tracker,
        pricing=pricing,
        model_configs=model_configs,
        seed=seed,
        manifest_path=manifest_path,
        max_per_batch=max_per_batch,
        fair_representation_candidates=fair_representation_candidates,
    )
    typer.echo("Run complete.")


@app.command()
def analyse(
    results_dir: Path = typer.Option(Path("runs/results")),
    figure_output: Path = typer.Option(Path("runs/figures/detection_by_severity.png")),
    table_output: Path = typer.Option(Path("runs/tables/detection_by_severity.tex")),
) -> None:
    """Load saved results, compute detection rates, generate figure + table."""
    results = load_results(results_dir)
    detection_rates = detection_rate_by_severity(results)
    plot_detection_by_severity(detection_rates, figure_output)
    latex = detection_rate_table_latex(detection_rates)
    save_table(latex, table_output)
    for severity, metrics in detection_rates.items():
        typer.echo(
            f"{severity}: precision={metrics['precision']:.2f}, recall={metrics['recall']:.2f}, f1={metrics['f1']:.2f}"
        )


if __name__ == "__main__":
    app()
