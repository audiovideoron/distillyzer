"""Distillyzer CLI - Personal learning accelerator."""

import typer
from rich.console import Console

app = typer.Typer(help="Distillyzer - Harvest knowledge, query it, use it.")
console = Console()


@app.command()
def search(query: str, limit: int = 10):
    """Search YouTube for videos on a topic."""
    console.print(f"[yellow]Searching YouTube for:[/yellow] {query}")
    console.print("[dim]Not yet implemented[/dim]")


@app.command()
def harvest(url: str):
    """Harvest a YouTube video or GitHub repo."""
    console.print(f"[yellow]Harvesting:[/yellow] {url}")
    console.print("[dim]Not yet implemented[/dim]")


@app.command()
def query(question: str):
    """Query your knowledge base."""
    console.print(f"[yellow]Querying:[/yellow] {question}")
    console.print("[dim]Not yet implemented[/dim]")


@app.command()
def chat():
    """Interactive chat with your knowledge base."""
    console.print("[yellow]Starting chat...[/yellow]")
    console.print("[dim]Not yet implemented[/dim]")


@app.command()
def stats():
    """Show statistics about your knowledge base."""
    console.print("[yellow]Knowledge base stats[/yellow]")
    console.print("[dim]Not yet implemented[/dim]")


if __name__ == "__main__":
    app()
