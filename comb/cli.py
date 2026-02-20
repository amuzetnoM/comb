"""CLI interface for COMB."""

from __future__ import annotations

try:
    import click
except ImportError:
    raise SystemExit(
        "COMB CLI requires 'click'. Install with: pip install comb-db[cli]"
    )

import json
from pathlib import Path

from .core import CombStore


@click.group()
@click.option(
    "--store", "-s",
    default="./comb-store",
    envvar="COMB_STORE",
    help="Path to the COMB store directory.",
    type=click.Path(),
)
@click.pass_context
def cli(ctx: click.Context, store: str) -> None:
    """COMB — Chain-Ordered Memory Base.

    Honeycomb-structured, lossless context archival for AI agents.
    """
    ctx.ensure_object(dict)
    ctx.obj["store"] = CombStore(store)


@cli.command()
@click.argument("text", required=False)
@click.option("--file", "-f", type=click.Path(exists=True), help="Read text from file.")
@click.option("--date", "-d", default=None, help="Override staging date (YYYY-MM-DD).")
@click.pass_context
def stage(ctx: click.Context, text: str | None, file: str | None, date: str | None) -> None:
    """Stage a conversation dump (Tier 2)."""
    if file:
        text = Path(file).read_text("utf-8")
    if not text:
        text = click.get_text_stream("stdin").read()
    if not text.strip():
        click.echo("Nothing to stage.", err=True)
        return
    ctx.obj["store"].stage(text, date=date)
    click.echo(f"Staged {len(text)} bytes.")


@cli.command()
@click.option("--date", "-d", default=None, help="Date to roll up (YYYY-MM-DD).")
@click.pass_context
def rollup(ctx: click.Context, date: str | None) -> None:
    """Roll up staged data into the chain archive."""
    doc = ctx.obj["store"].rollup(date=date)
    if doc is None:
        click.echo("Nothing staged to roll up.", err=True)
        return
    click.echo(f"Archived {doc.date} | hash: {doc.hash[:16]}... | "
               f"semantic: {len(doc.semantic.neighbors)} | "
               f"social: {len(doc.social.links)}")


@cli.command()
@click.argument("query")
@click.option("--mode", "-m", default="bm25", type=click.Choice(["bm25", "semantic", "hybrid"]))
@click.option("-k", default=5, help="Max results.")
@click.pass_context
def search(ctx: click.Context, query: str, mode: str, k: int) -> None:
    """Search the archive."""
    results = ctx.obj["store"].search(query, mode=mode, k=k)  # type: ignore[arg-type]
    if not results:
        click.echo("No results.")
        return
    for doc in results:
        click.echo(f"  {doc.date}  score={doc.similarity_score:.4f}  "
                   f"({doc.metadata.get('byte_size', '?')} bytes)")


@cli.command()
@click.argument("date")
@click.pass_context
def show(ctx: click.Context, date: str) -> None:
    """Show an archived document."""
    doc = ctx.obj["store"].get(date)
    if doc is None:
        click.echo(f"No document for {date}.", err=True)
        return
    click.echo(json.dumps(doc.to_dict(), indent=2))


@cli.command()
@click.pass_context
def stats(ctx: click.Context) -> None:
    """Show store statistics."""
    s = ctx.obj["store"].stats()
    click.echo(json.dumps(s, indent=2))


@cli.command()
@click.pass_context
def verify(ctx: click.Context) -> None:
    """Verify chain integrity."""
    ok = ctx.obj["store"].verify_chain()
    if ok:
        click.echo("✓ Chain integrity verified.")
    else:
        click.echo("✗ Chain integrity FAILED.", err=True)
        raise SystemExit(1)


@cli.command()
@click.option("-k", default=5, help="Number of recent documents to recall.")
@click.option("--no-staged", is_flag=True, help="Exclude un-rolled staged entries.")
@click.pass_context
def recall(ctx: click.Context, k: int, no_staged: bool) -> None:
    """Reconstruct operational context (wake-up half of blink)."""
    text = ctx.obj["store"].recall(k=k, include_staged=not no_staged)
    click.echo(text)


@cli.command()
@click.argument("text", required=False)
@click.option("--file", "-f", type=click.Path(exists=True), help="Read text from file.")
@click.option("--rollup", "-r", is_flag=True, help="Also roll up into archive.")
@click.pass_context
def blink(ctx: click.Context, text: str | None, file: str | None, rollup: bool) -> None:
    """Stage a memory flush for seamless agent restart.

    The blink pattern: flush context → restart → recall → resume.
    Call this before restarting your agent. On wake-up, call `recall`.
    """
    if file:
        text = Path(file).read_text("utf-8")
    if not text:
        text = click.get_text_stream("stdin").read()
    if not text.strip():
        click.echo("Nothing to blink.", err=True)
        return
    recall_text = ctx.obj["store"].blink(text, rollup=rollup)
    click.echo(f"Blinked {len(text)} bytes. Recall preview:")
    click.echo(recall_text[:500] + ("..." if len(recall_text) > 500 else ""))


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
